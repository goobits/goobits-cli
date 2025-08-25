interface CommandArgs {
    commandName: string;
    rawArgs?: Record<string, any>;
    [key: string]: any;
}
export declare function onUnknownCommand(args: CommandArgs): Promise<void>;
export declare function onGreet(args: CommandArgs): Promise<void>;
export declare function onInfo(args: CommandArgs): Promise<void>;
export {};
//# sourceMappingURL=hooks.d.ts.map